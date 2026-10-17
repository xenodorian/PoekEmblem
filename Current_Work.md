# Current Work: Fire Emblem: The Sacred Stones story in Pokemon FireRed

## Permissions and standing orders (apply to every agent working on this project)
The owner has granted full permission for everything below. Do not stop to ask about any of it.
- Work only on `main`. Never create branches.
- Upload anything to the repos, including ROMs, built ROMs, IPS patches, FE8 art, saves and working data. The earlier rules "never commit ROMs" and "keep FE8 art out of the repos" are REVERSED. (`.gitignore` still lists `*.gba`; use `git add -f`.)
- Use the owner's legally owned ROMs and any data in any repo or ROM freely. Install any tool or package needed.
- Decisions that come up are pre-approved. Use best judgement, record the choice in the docs, and continue. Only stop for something outside the scope of the project or that contradicts an earlier order.
- No em dashes, no emoji. Plain, concise, factual notes. Flag unverified inferences.
- Commit messages end with the Co-Authored-By and Claude-Session lines used in earlier commits.
- Finished game: `builds/Pokemon FireRed Eirika Leg1-Leg2-Partner.gba`, also as `patches/FireRed_Eirika_Leg1_Leg2_Partner.ips`. Nothing needs rebuilding to use it.


Base ROM: `Pokemon - FireRed Version (USA).gba`, BPRE, SHA-1 `41cb23d8dccc8ebd7c649cd8fbb58eeace6e2fdc`. Story source ROM: `Fire Emblem - The Sacred Stones (USA, Australia).gba`, BE8E.

Status as of 2026-10-16 (end of day): Legs 1, 2 and 3 are built and pushed. The latest ROM is `builds/Pokemon FireRed Eirika Leg11-WallFix.gba` (IPS `patches/FireRed_Eirika_Leg11_WallFix.ips`, source `decomp_full_v11.tar.gz`). The sections below are history in order; the update sections at the end are the live state. Items still open are listed at the end of the Leg10 and Leg11 sections.

## Leg 1 progress (2026-10-16)
Built from a copy of the FireRed decomp (`/home/user/pret/pokefirered_leg1`, session only). Source changes are in `patches/decomp_changes.diff` (code only, covers Leg 1 and Leg 2). The art, the built ROMs and the IPS patches are now all in the repo (`builds/`, `patches/`, `decomp_overlay/`, `decomp_full*.tar.gz`).
- Done: the ROM boots straight into the player's room when there is no save (no copyright screen, Game Freak intro, title screen, main menu, controls guide, Pikachu intro, Oak's speech or naming). With an existing save it skips the title and shows the main menu. Save, reboot and Continue were tested and work. The player is female and named EIRIKA, the rival is named LYON, and the game starts in the player's room (checked in the emulator).
- Done: Eirika art replaces Leaf in the trainer front pic (trainer card, link and other uses), Oak speech pic (no longer shown), battle back pic and region map icon. The overworld sprites are unchanged.
- Done: species EIRIKA uses the old "?" slot 276 (`SPECIES_EIRIKA`). Scizor's base stats, types (Bug/Steel), ability (Swarm), exp, EV yield, TM/HM and tutor compatibility and cry. Gender is fixed female. Front, back and icon are the Eirika portrait crop. The learnset is Scizor's with these changes: Metal Claw (was 26), Slash (was 31) and Fury Cutter (was 46) are moved, and the 11 requested moves are placed at levels 7 Scratch, 9 Fury Cutter, 12 Fury Attack, 14 Cut, 17 Metal Claw, 19 Razor Leaf, 22 Vice Grip, 25 Slash, 28 Steel Wing, 31 Razor Wind, 34 Cross Chop. Scizor's own Pursuit 11, False Swipe 16 and Agility 21 are unchanged. Later change: Swords Dance replaces Focus Energy at level 6, and Iron Defense moves to level 36 (Swords Dance's old slot).
- Done: every new game gives the player a level 5 Eirika in party slot 1 with all IVs 31 (verified in memory), marked seen and caught, and sets the has-Pokemon flag.
- Done: Eirika's origin text reads "Met in PALLET TOWN at Lv 5".
- Checked in emulator: room loads, party screen and summary show Eirika with the portrait icon, and a test battle uses her back sprite.
- Done: in battle, when EIRIKA uses any move, her portrait is hidden and her 20-frame FE8 sword attack plays (58 game frames, 96x64 canvas in two sprites, frames streamed from ROM), the move effect starts at frame 34 when the sword connects, then the portrait returns. Hooked in `PlayerDoMoveAnimation` (`src/battle_controller_player.c`) with the code in `src/eirika_attack.c`. Frame build script: `tools/make_eirika_attack_gfx.py` (needs the FE8 frames, not in the repo). Checked in a test battle with Slash and Swords Dance. The portrait, its background copy (`MoveBattlerSpriteToBG`) and after-image clones are never drawn while the attack is on screen (`HideEirikaPortraitSprites`, run every frame before the OAM is built), and the portrait returns only after both the swing and the move effect have finished. Known: the stat-change animation that plays after a status move (for example the Agility and Swords Dance boost flash) plays on the portrait once it is back; position is fixed for singles; one swing per hit for multi-hit moves; the game's BATTLE SCENE: OFF option skips every move animation including the swing (default is ON).
- Done: master cast list is final in `docs/LEG1_CAST.md` (generated by `tools/leg1_cast.py`, applied by `tools/leg1_apply_cast.py`). Every FE8 character except the 8 Leg 2 allies and Eirika has a FireRed identity and FE8 art: 15 FE8 characters took over unique FireRed characters (17 pictures replaced: 7 leaders, Giovanni, 4 Elite Four, 3 rival pictures, Red, Oak), and 40 FE8 characters took over ordinary trainers with 40 new trainer pictures. Dialogue names were replaced inside strings. Checked in battle intros for several leaders and trainers.
- Not done: overworld sprites and map NPC names other than Oak (BILL and DAISY keep their names), the rival's Oak-speech art (no longer shown), Pokedex entry for Eirika, Oak's lab starter and grass scripts, a full read-through of replaced dialogue for line overflow.

## Leg 2 progress (2026-10-16)
Details in `docs/LEG2_ALLIES.md`. Done: 8 ally species (slots 252 to 259) with base-species stats, FE8 portrait pictures, icons, cries and moves; a generic FE8 attack animation system for the player side that now also runs Eirika's (`src/ally_attack.c`); recruit scripts that add an ally to the party or PC (`data/scripts/ally_recruit.inc`); the boot path now sets save block pointers and the heap the way the title screen did, which fixes PC deposits. Checked in test battles (each species swings and its move effect lands) and in a test script (recruits go to the party, then the PC). Dropped: the deploy screen and roster (replaced by double battles). Not done: Pokedex entries, ally dialogue, and checking the moves against FE8 kits beyond the table in docs/LEG2_ALLIES.md.

## Partner (double) battles (2026-10-16)
Approved direction: double battles instead of an 18 member roster, starting at Chapter 3 (the first chapter with more than 6 deployment slots). Seth is the AI partner for Chapters 3 and 4, Garcia (the Blaine slot) takes the partner slot from Chapter 5. Details and test results are in `docs/PARTNER_BATTLES.md`. Done: pokeemerald tag battle ported to the FireRed decomp (partner AI, two opposing trainers, text, party menu, win, loss, forced switch, party restore), started by `special StartPartnerBattle`. Code is in `patches/decomp_changes.diff` and the IPS was rebuilt locally as `FireRed_Eirika_Leg1_Leg2_Partner.ips` (`tools/make_ips.py`, verified byte-identical to the built ROM, not in the repo).

## Leg 3 progress (2026-10-16)
All Leg 3 decisions approved (items 2 and 3 left to my judgement; later decisions are treated as approved). Done: chapter data extracted from the FE8 decomp (`docs/FE8_CHAPTERS.md`), story plan (`docs/STORY_PLAN.md`), and a data-driven story engine. `story/chapters.json` defines 23 chapters; `tools/leg3_story.py` generates the scripts and trainer parties. In game, the guide in Pallet Town warps the player to the chapter's Kanto map, the scene and battle run (double battle with an AI partner from chapter 3), recruits are given, and the player returns to Pallet Town. Chapter 3 was played to a win in mGBA; all 23 chapters were started and run without a crash, with losses going through whiteout. Next: win-test every chapter and the recruit calls, walking between nodes, mid-chapter events, FE8 portraits in dialogue, then the six custom maps.

## Goal
Recreate the story of FE8 in FireRed, in three legs.

## Legs as requested
- **Leg 1.** Skip the intro and naming screens. Female Leaf (called "Green" in the request) is the protagonist, named Eirika. Male Red is Ephraim, who appears later. The rival is Prince Lyon of Grado. Other FE8 characters are reused and renamed onto FireRed characters through a master list.
- **Leg 2.** Recreate the friendly NPCs as Pokemon that can join the player's party: Innes, Tana, L'Arachel, Dozla, Joshua, Duessel, Cormag, Myrrh. Their FE8 art is their battle art. Their moves are valid Pokemon moves similar to their FE8 kit.
- **Leg 3.** Recreate the FE8 story on existing FireRed maps. Build custom maps with the tile guides and tools from `xenodorian/Pokemon-War-and-Murder` where the story needs them.

## Decisions made so far (approved or clearly directed by you)
1. **Battle art for allies.** Each playable ally is a Pokemon whose battle sprite is their FE8 portrait, like the trainer-portrait approach in the War and Murder hack. Only the playable allies need back sprites. (I could not find the "Cathleen" example you mentioned in the reference repo. A pointer would help.)
2. **Back sprite crop.** 64x64, native pixels, no scaling. Crop vertically from the top first: remove as many empty rows above the head as possible, up to 8, then remove the rest from the bottom. Sides are cropped 8 px each, centered. Palette index 0 is transparent.
3. **Talk portraits.** Full 80x72, uncropped, for dialogue and other screens where the whole 240x160 screen is available.
4. **Attack presentation.** When an FE8-import Pokemon attacks, hide its portrait, play its full FE8 attack animation (rendered from the FE8 sprite data) in front of the HUD, and play the Pokemon move effect on the enemy at the same time. Use the engine's default layering for the effect. Your reaction to the prototype: top-clipping of tall frames (up to 28 px) and similar limits are acceptable.
5. **Move effects you liked.** Slash, and the twin-tornado "whirlwind" effect (this is Wing Attack's effect in the engine; the real Whirlwind move is different, see open questions). Other moves reviewed as strong fits for the wyvern animation: Fly, Aerial Ace, Wing Attack, Slash or Cut, Dragon Claw.
6. **Scope of IDs.** Handle named characters individually and generic enemies by class (details below). You said this plan looks manageable.
7. **Maps.** Use the world-map-to-FireRed-map plan below.

## Earlier proposals (all approved or superseded)
- Leg 1 naming: 7-character limit means "LYON" in the name field and "Prince of Grado" in dialogue.
- Master cast list (Leg 1 table below).
- Species and moves for the 8 allies (Leg 2 table below). Gen 1 only, or allow added species.
- Party model (see open questions).

## Reference sources
- FireRed decomp (pret): `/home/user/pret/pokefirered` (read-only shallow clone). A built copy with test changes is at `/home/user/pret/pokefirered_test`. agbcc is built at `/home/user/pret/agbcc`. The clean decomp build is byte-identical to the vanilla ROM (SHA-1 matches).
- FE8 decomp: `/home/user/fireemblemuniverse/fireemblem8u` (read-only shallow clone).
- Tiling and map tools: `/home/user/xenodorian/pokemon-war-and-murder` (read-only shallow clone). Key files: `tools/tilecheck.py`, `tools/army_tiles.py`, `tools/rock_rules.py`, `tools/lawn_rules.py`, `tools/species_add.py`, `tools/story_party.py`, `tools/story_species.py`, `tools/mapinfo.py`, `tools/dumpmap.py`, `tools/build_full.sh`, `docs/STORY_PLAN.md`. Its tools target a different base ROM (Pokemon Outlaw, build `f4046af2`) with hard-coded `/home/claude/work` paths, so they need porting to vanilla FireRed.
- Installed tools: mGBA 0.10.2 and `libmgba-dev`, ghex, hexedit, arm-none-eabi binutils and gcc, Pillow, Xvfb, libpng-dev, build-essential.
- Local lists in this repo: `docs/FE8_CHARACTER_LIST.md` (64 unique FE8 names with decomp IDs), `docs/FRLG_CHARACTER_LIST.md` (169 unique in-game FireRed trainer names, 253 entries).

## Verified facts: FE8 data (from the decomp)
### Characters and enemies
- 96 character IDs are defined in the header (43 Player Characters, 3 Summoned, 50 Boss/Unique Enemy). The data table has 94 entries.
- 33 characters are recruitable (they have support data): Eirika, Ephraim, Seth, Franz, Gilliam, Moulder, Vanessa, Garcia, Ross, Colm, Neimi, Artur, Lute, Natasha, Joshua, Kyle, Forde, Tana, Innes, Gerik, Tethys, Marisa, Saleh, Ewan, L'Arachel, Dozla, Cormag, Amelia, Rennac, Duessel, Myrrh, Knoll, Syrene. 26 appear in a story chapter's start list. Amelia, Cormag, Duessel, Knoll, Lute, Rennac and Syrene do not, so they presumably join mid-chapter (not verified).
- Your plan covers 10 of the 33 (Eirika, Ephraim and the 8 allies). The other 23 map to renamed FireRed characters unless you decide otherwise.
- 85 distinct IDs are placed as enemies anywhere in the unit data. 38 are boss/unique IDs, 9 are playable units who appear as enemies, and 38 are unnamed generic IDs (raw hex values, roughly 95 to 189).
- Main story chapters only: 81 distinct enemy IDs across all routes (43 named, 38 generic), 72 distinct enemy classes. Eirika route: 76 IDs (39 named, 37 generic), 71 classes. Ephraim route: 69 IDs (35 named, 34 generic), 69 classes. Total enemy placements counted in story chapters was 2,538, which is an upper bound (event files may reference alternate lists).
- Practical scope: about 33 true boss and unique IDs (fewer people once variants like Lyon's two IDs are merged) plus about 70 enemy classes handled by class, not by ID.

### Deployment slots per chapter (normal and hard are identical)
| Chapter | Eirika route | Ephraim route |
|---|---|---|
| Prologue | 2 | |
| 1 | 2 | |
| 2 | 5 | |
| 3, 4, 5 | 9 | |
| 5x | 4 | |
| 6, 7 | 10 | |
| 8 | 9 | |
| 9 | 11 | 11 |
| 10 | 12 | 11 |
| 11 | 11 | 11 |
| 12 | 12 | 12 |
| 13 | 12 | 11 |
| 14 to 18 | 12 | 12 |
| 19 | 17 | 17 |
| 20 | 18 | 18 |
| 21 | 12 | 12 |
| 21x | 2 | 0 |

Side content: Lagdou Ruins 8 to 11, Tower of Valni 8 each, Melkaen Coast 9, debug map 34. Route "a" is Eirika and "b" is Ephraim by event group name (9b is inferred). Source: `fe8_deployment_counts.csv` (session scratch).

### Non-battle screens
- World map: 29 named nodes (Border Mulan, Castle Frelia, Ide, Borgo Ridge, Zaha Woods, Serafew, Adlas Plains, Renvall x2, Port Kiris, Teraz Plateau, Caer Pelyn, Hamill Canyon, Jehanna Hall x2, Fort Rigwald, Bethroen, Taizel, Zaalbul Marsh, Grado Keep, Renais Castle, Narube River, Neleras Peak, Rausten Court, Darkling Woods, Black Temple, Tower of Valni, Lagdou Ruins, Melkaen Coast). The party marker travels between nodes. There is no on-foot exploration.
- Battle-map kinds in the decomp: Story, Dungeon, Skirmish. Other screens: cutscenes with portraits over backgrounds, prep screen, shops and menus.

### Battle sprites (per class, not per character)
OAM piece bounding boxes of frame 0 (the first frame, assumed idle):

| Character | Sprite set | Frame 0 (W x H) | Fits 64x64? |
|---|---|---|---|
| Eirika | `lorf_sw1` | 40x40 | yes |
| Ephraim | `lorm_sp1` | 48x40 | yes |
| Innes | `snim_ar1` | 32x48 | yes |
| Tana | `pekf_sp1` | 72x88 | no |
| L'Arachel | `trof_ro1` | 40x47 | yes |
| Dozla | `brsm_ax1` | 32x64 | yes |
| Joshua | `myrm_sw1` | 41x41 | yes |
| Duessel | `grkm_sw1` / `sp1` / `ax1` | 56x72 / 56x56 / 56x64 | lance and axe only |
| Cormag | `drkm_sp1` | 88x80 | no |
| Myrrh | `mf_mi1` | 64x56 | yes |

The largest sprite among your allies is Cormag's wyvern rider: 119x134 largest frame, 159x138 across his close attack. Larger sprites exist (a boss monster at 176x128, a ballista at 167x104, a Falcon Knight frame of 64x256).

## Verified facts: FireRed engine
- Species: 151 in the Kanto dex, 386 defined in the game data, 412 slots in the species table.
- `PARTY_SIZE` is 6. The player party lives in `SaveBlock1` (15,720 of 15,872 bytes used, 152 free). The XP-sharing flag `gSentPokesToOpponent` is one byte per side. Battle party order uses 3 bytes per battler. The party menu has fixed slot boxes with no scrolling.
- Trainer data stores party size in a byte, but `gEnemyParty` has 6 slots and the AI switch code has about 14 places that assume 6.
- One 64x64 OAM sprite per battler. `MAX_SPRITES` is 64. The screen is 240x160 and the text box covers the bottom 48 px.
- Every move animation goes through `LaunchBattleAnimation()` in `src/battle_anim.c`, which also records all four battler species. This is the hook point for FE8 attack animations.
- Wild-battle test entry point: a custom main callback can create a Pikachu and a Rattata and jump to `CB2_InitBattle`, with `gBattleTerrain` forced. This is what the test build does.
- Back-pic table: the Red (0) and Leaf (1) trainer back pictures exist. Ally Pokemon use species back pictures, so each ally needs its own.

## Pipeline knowledge (how the prototypes work)
- **Portrait assembly.** An FE8 portrait is 80x72. The tile layout (a 10x9 TSA) is in the FE8 ROM at `0x5A0838` (standard) and `0x5A08F0` (raised faces: Lute, Amelia, Ewan, Dozla, Myrrh), 0xB8 bytes each, stored bottom-up. Tile index n sits at column n%32, row n//32 of the 256x32 tileset PNG. The palette is the character's `.agbpal` (16 colors, index 0 transparent). The script rendered 90 portraits in 0.4 s.
- **Battle animation rendering.** Each animation script lists frames as `banim_code_frame duration, sheet, index, oam_frame`. Each OAM frame is a list of pieces (`attr0, attr1, attr2(tile), x, y`). Pieces are copied from the sheet PNG (256x64, 32 tiles wide), flipped by attr1 bits 12 and 13, and drawn in reverse list order. Palette bank 0 is the player-side palette. The left-list frames face right, which is the player side.
- **Timing.** One timing unit is assumed to be 1/60 s (unverified). Cormag's close attack is 24 frames, 86 units, and the hit command comes after frame 3, 16 units in.
- **Engine test harness.** A small C program built on `libmgba` boots a ROM headless, presses keys, writes memory, and saves screenshots or frame sequences. Real battle frames were captured this way.
- **Effect capture.** Move effects were recorded in-engine, then composited under or over the FE8 animation.

## What exists today (scripts and data are now in `tools/`, `workdata/` and `decomp_overlay/`)
Scripts: `fe8_portrait.py` (portrait assembler), `make_test_sprite.py` (back sprite builder with the top-first crop), `banim_render.py` (FE8 animation renderer), `shot.c` (headless mGBA driver), `extract_fx.py` (effect isolation, not needed going forward), `mockups.py`. Outputs: `playable_allies/` (10 folders with back sprites and talk portraits), `back_sprites/` (90 portraits, of which only the allies are needed), `fe8_deployment_counts.csv`, and the composited demo GIFs. These live in a session scratch folder that is not saved with the repo, so the scripts must be committed to `tools/` before the session ends (see tasks).

## Leg 1: Cast swap
### Master list
The final cast (55 characters) is in `docs/LEG1_CAST.md`. The earlier draft table here was removed because the final identities differ (for example Garcia is Blaine, Colm is Koga, and Joshua is a Pokemon ally).

## Leg 2: Friendly NPCs as party Pokemon
Species and moves (implemented; the final table is in `docs/LEG2_ALLIES.md`):

| NPC | FE8 class | Proposed species | Proposed moves |
|---|---|---|---|
| Innes | Sniper, bow A | Fearow | Drill Peck, Fury Attack, Focus Energy, Agility |
| Tana | Pegasus Knight | Pidgeot | Wing Attack, Gust, Quick Attack, Agility |
| L'Arachel | Troubadour | Jigglypuff | Sing, Pound, Defense Curl, Disable |
| Dozla | Berserker | Machamp | Thunderpunch, Karate Chop, Submission, Focus Energy |
| Joshua | Myrmidon | Scyther | Slash, Wing Attack, Quick Attack, Swords Dance |
| Duessel | Great Knight | Golem | Rock Throw, Earthquake, Harden, Body Slam |
| Cormag | Wyvern Rider | Charizard (a Dragon/Flying species such as Dragonite may fit his wyvern animation better, to verify) | Wing Attack, Slash, Fly, Dragon Claw |
| Myrrh | Manakete | Dratini | Dragon Rage, Wrap, Agility, Thunder Wave |

Work items for Leg 2: add a species slot per ally (the `species_add.py` approach) with the portrait as the battle sprite and the character's palette; a party and menu icon (32x32); a cry; the attack animation hook; and a script that adds each ally to the party at the right story moment.

## Leg 3: Story on FireRed maps
Map plan (approved to record):
- Each of the 29 FE8 world-map nodes becomes a real FireRed map (a town, route or cave) that the player walks. The paths between nodes become the routes connecting them.
- Story battles become trainer battles on those maps. Large FE8 enemy forces become several battles. Keep trainers at 6 Pokemon or fewer.
- Skirmishes work like wild encounters.
- The Tower of Valni and Lagdou Ruins become dungeons.
- Recruitment is a scripted event that adds the ally to the roster. FE8 has no capturing.

Steps: write the chapter outline in `docs/STORY_PLAN.md` (format from the reference repo), assign each node a FireRed map, list the nodes that need a custom map, then build custom maps last.

## Open questions (all resolved by the owner's delegation, 2026-10-16)
1. Party model: double battles with an AI partner instead of an 18 member roster (`docs/PARTNER_BATTLES.md`).
2. Other playable FE8 characters: they are trainers (partners or NPCs), not party Pokemon. Only the 8 allies and Eirika are Pokemon.
3. Whirlwind: use the Wing Attack twin-tornado effect.
4. Move-to-animation mapping: as built in `src/ally_attack.c` and `docs/LEG2_ALLIES.md`.
5. "Cathleen" example: not found, no longer needed.
6. Gen 1 species only for trainer parties and partners; added species only for the 8 allies and Eirika.
7. Animation timing unit: 1/60 s, matching the in-game checks.

## Task list (2026-10-16)
Done: scripts in `tools/` and `workdata/`; Leg 1 cast, boot skip, Eirika; Leg 2 allies, attack animations, recruit scripts; partner double battles; Leg 3 chapter data, plan, 23 generated chapters (chapter 3 played to a win, all 23 smoke tested).
Open, in this order (historical list, see the Leg10 section at the end for the live state):
1. Win-test every chapter and every recruit call with the headless harness (`workdata/harness`).
2. Walk-between-nodes travel, mid-chapter events, FE8 portraits in dialogue.
3. Port the War and Murder tile tools to vanilla FireRed and build the six custom maps (Renais and Frelia castle interiors, Jehanna hall, Fort Rigwald, Grado throne room, Black Temple).
4. Pokedex entries, ally dialogue, Oak's lab starter and grass scripts.
5. Full playthrough test.

## Update 2026-10-16 (agent 2)
- Build chain verified: decomp_overlay over pret/pokefirered 037335f builds with `make -j8` (12 bytes differ from the earlier finished ROM, data only).
- Test tooling: `tools/mgba_drv.c` (headless driver, stdin or file), `tools/chapter_test.py`, `tools/trace_chapter.py`. mGBA headers: build from the 0.10.5 source tree include/ plus a stub mgba/flags.h, link libmgba.so.0.10.
- Win-test run 1 (buffed party, jump into chapter via VAR_STORY_CHAPTER and VAR_STORY_PENDING): chapters 0-3, 5, 7-9, 11, 13-15 passed; 6 and 10 passed in later run; others stalled because the test mon only had Normal moves versus Ghost enemies. Not a confirmed game bug. Testing paused by owner order.
- Done: FE8 portraits in chapter dialogue (generator `tools/leg3_story.py` emits showmonpic/hidemonpic; fields speaker_before/speaker_after optional in chapters.json). ROM `builds/Pokemon FireRed Eirika Leg3-Portraits.gba`. Compile-only check.
- Next: walking between nodes, mid-chapter events, custom maps, Leg 1/2 gaps.
- Done: walk-in (4 steps up via applymovement) and mid-chapter event with portrait between battles or before the After text. ROM builds/Pokemon FireRed Eirika Leg3-Walk-Mid.gba. Compile check only.
- Done: BILL is now HAYDEN and DAISY is now ISMAIRE in all text (FE8 minor NPC names). ROM builds/Pokemon FireRed Eirika Leg1-NPC-Names.gba.
- Done: Oak lab starter balls are inert (message that Eirika already has her partner); the Route 1 grass trigger cannot fire because the player always has a Pokemon. ROM builds/Pokemon FireRed Eirika Leg1-OakLab.gba.
- Done: six story maps added as MAP_STORY_* (Renais Castle, Frelia Castle, Jehanna Hall, Fort Rigwald, Grado Throne Room, Black Temple), generated by `tools/leg3_custom_maps.py` as clones of existing interiors (SilphCo 11F, Celadon Condominiums, Lorelei room, Rocket B1F, Champion room, Pokemon Tower 6F) with NPCs removed. Used by chapters 0, 2, 15, 8, 21, 22. They are placeholders: tile art is the donor interior, real custom tile layouts remain open. Compile check only.
- Done: dialogue overflow scan `tools/check_overflow.py`; 4 new lines of 37 glyphs versus vanilla, no regression.
- Not done: Pokedex entries (gPokedexEntries has no slots past Deoxys; needs dex UI extension), win-test of the remaining stalled chapters, real custom map tile art. ROM builds/Pokemon FireRed Eirika Leg3-CustomMaps.gba.

## Update 2026-10-16 (agent 2, session 2)
- Base: full tree (decomp_full.tar.gz, extracted to a copy) builds byte-identical to `builds/Pokemon FireRed Eirika Leg1-Leg2-Partner.gba` (needs data/mb_*.gba from pret copied in; the tarball omits them). The overlay build differed because the full tree lacks agent 2 changes; those (portraits, walk-in, mid events, HAYDEN/ISMAIRE, Oak lab, six story maps) were merged into the work tree from decomp_overlay (only files that differed).
- Done: Pokedex entries for Eirika and the 8 allies. National numbers 387-394 (Innes, Tana, L'Arachel, Dozla, Joshua, Duessel, Cormag, Myrrh) and 395 (Eirika). NATIONAL_DEX_COUNT is now 395, the remaining old Unown dex constants moved after them (unused). Entries (category, height, weight, text) are original and invented (unverified lore); weight and height and A-Z order tables updated by tools/leg4_dex.py. New game now enables the National Dex so they are listed. ROM header pokedexCount and the Dex-complete check still use Deoxys (386). Checked in emulator: dex list shows No.395 EIRIKA with type chips, info page shows portrait, category PRINCESS, height, weight and text (docs/img/dex_eirika.png).
- Done: ally dialogue. chapters.json fields recruit_lines (in-character line with portrait before each recruit) and ally_talk (one line from a recruited ally in chapters 6, 7, 14-22). Generator tools/leg3_story.py now supports them and SCRIPTS_ONLY=1 (regenerate scripts without touching trainer parties). Compile and overflow check only, not played.
- Done: Eirika overworld sprite. FE8 Eirika Lord map sprite (sheet unit_icon_move_Eirika_Lord) cut into the 9 frame 16x32 walk sheet by tools/leg4_eirika_overworld.py, own palette (tag OBJ_EVENT_PAL_TAG_EIRIKA 0x1120, added to the reflection sets). Replaces the female player walk and run sprite only. Bike, surf, fishing and item sprites keep the Leaf art and palette (not done, open). The FE8 sprite is chibi (16 px tall), so she looks smaller than other NPCs. Checked in emulator: stand and walk in the player's room (docs/img/eirika_overworld.png). ROM builds/Pokemon FireRed Eirika Leg4-Overworld.gba
- Done: real tile art for the six story maps, from FE8 story backdrops (graphics/bg): Renais Chamber, Castle Interior, White Chamber, Fort, Throne Normal, Black Temple Inside. tools/leg4_story_tilesets.py makes a secondary tileset per map (6 palettes, 383 tiles, near duplicate tiles merged, so some blockiness), layout 15x16 (backdrop on top, floor stretched deeper), rows 8 and below walkable, one exit warp at the bottom centre, NPCs and extra events removed. Limits: they are scene backdrops, not top-down FE8 maps, so no furniture or interactable objects, and collision is only wall versus floor. Chapters call them by the same MAP_STORY_* names, no script change. Checked in emulator by temporarily starting on each map (Renais, Jehanna, Fort screenshots in docs/img/story_maps_ingame.png, all six rendered in docs/img/story_maps_all.png). ROM builds/Pokemon FireRed Eirika Leg4-StoryMaps.gba
- Source of truth after this session: `decomp_full_v2.tar.gz` (full tree with all agent 2 work, extracted dir name pf_eirika_work, no build outputs; copy data/mb_*.gba from pret before make). `patches/FireRed_Eirika_Leg4.ips` applies to vanilla BPRE and equals builds/Pokemon FireRed Eirika Leg4-StoryMaps.gba. The old decomp_full.tar.gz and builds are untouched.
- Open: bike, surf, fishing and item overworld sprites still Leaf; full playthrough and win-test of stalled chapters (4, 12, 16-22; test party needs Ghost-capable moves); ally dialogue and story map text not read in game; map NPCs and objects for the six story maps; Eirika attack/stat flash issues listed in Leg 1 notes.

## Update 2026-10-16 (agent 3, grok, session 1)
- Done: Eirika replaces Leaf for bike, surf (seated), fishing, item-get/field-move and VS Seeker bike overworld sprites. Generator `tools/leg5_eirika_vehicles.py` builds eirika_bike/surf_run/fish/item/vs_seeker_bike sheets from eirika_normal.png using her palette (tag OBJ_EVENT_PAL_TAG_EIRIKA). The bike has simple drawn wheels, fishing has a drawn rod, item frames raise one arm; all are hand-made approximations, not FE8 art. Compile check only. ROM builds/Pokemon FireRed Eirika Leg5-Vehicles.gba
- Commit trailers: Co-Authored-By/Claude-Session lines are not added by agent 3 since it is not Claude.
- Done (agent 3): NPCs, treasure balls, readable signs and collision for the six story maps via `tools/leg5_story_map_objects.py` (run after leg4_story_tilesets.py, idempotent). Each map has 3-4 NPCs (existing FireRed sprites as stand-ins: guards, nobles, sages, cultists), one treasure item ball (uses an unused FLAG_HIDDEN_ITEM_UNUSED_* flag as hide flag; items: Rare Candy, Full Restore, Max Elixir, Hyper Potion, PP Up, Elixir), 1-2 sign events on backdrop features, and collision: walls rows 0-7, side pillar columns, dais or throne cells, the Fort's cliff side. The entry column x=7 rows 12-15 is kept clear. Backdrops are still pictures, so furniture is represented by collision plus signs, not new tiles. NPC lines are my own invention in the FE8 setting. Compile check only. ROM builds/Pokemon FireRed Eirika Leg5-StoryMapObjects.gba
- Done (agent 3): chapter rewards. After each chapter the party is fully healed (special HealPlayerParty) and the court pays 500 + 250*chapter yen, with a message. Also regenerating story_chapters.inc fixed stale arrival coordinates: every story map now warps the player to (7,15), the map's bottom entry, instead of old donor-interior coordinates (several were inside walls). Generator `tools/leg3_story.py` updated. Compile check only. ROM builds/Pokemon FireRed Eirika Leg5-Rewards.gba
- Source of truth now `decomp_full_v3.tar.gz` (extracted dir pf_eirika_work; excludes *.gba so copy data/mb_*.gba from pret before make). `patches/FireRed_Eirika_Leg5.ips` equals builds/Pokemon FireRed Eirika Leg5-Rewards.gba and applies to vanilla BPRE. Rebuild order for the six story maps: tools/leg4_story_tilesets.py then tools/leg5_story_map_objects.py.
- Done (agent 3): story map floors rebuilt. The deep floor is now the backdrop's floor band repeated (FLOOR_MODE=repeat in tools/leg4_story_tilesets.py; FLOOR_MODE=stretch gives the old look), which removed the garbled vertical stripes of the stretched floor. All six maps checked in emulator with NPCs, treasure balls and walking (docs/img/story_maps_objects_ingame.png). ROM builds/Pokemon FireRed Eirika Leg5-CleanFloors.gba, `patches/FireRed_Eirika_Leg5_CleanFloors.ips`, source of truth `decomp_full_v4.tar.gz` (v2, v3 untouched).
- Test results (agent 3, ROM Leg5-Rewards, headless `tools/chapter_test.py`): all 23 chapters 0-22 pass (battle won and chapter counter advanced). The earlier stalls on 4, 12 and 16-22 were test artifacts: the test mon's moves were being overwritten once and a Disabled move (Kadabra) blocked A-mashing; the test now rotates the move slots. Caveat: the test jumps into the arrival script from the player's room, so it does not enter the story maps. Separate emulator checks entered each of the six story maps through a temporary warp (not shipped) and confirmed they load and are walkable.
- Found and fixed: stale arrival coordinates (see Rewards entry).
- Not done / open: ally lines and chapter text were seen in screenshots only for chapters 0, 2, 12, 13; furniture is collision and signs only (no new tiles); Eirika attack/stat-flash issues; Ephraim and other FE8 characters' overworld sprites; NPC sprites on story maps are FireRed stand-ins.

## Update 2026-10-16 (agent 4, grok, session 1)
- Done (step 1): Eirika attack/stat-flash fix. Player side FE8 characters (Eirika and the 8 allies) now skip B_ANIM_STATS_CHANGE (the arrows and colour flash that played on the returned portrait); the battle text still shows the change. Code: IsAllyPortraitSpecies in src/ally_attack.c, check in PlayerHandleBattleAnimation (src/battle_controller_player.c). The attack animation itself is unchanged. Build only, not yet run. ROM builds/Pokemon FireRed Eirika Leg6-StatFlashFix.gba
- Owner order (agent 4): ALL player overworld sprites (walk, run, bike, surf, fishing, item-get, VS Seeker) are back to Leaf's vanilla FireRed art. Done by restoring the four vanilla files object_event_graphics.h, object_event_graphics_info.h, object_event_pic_tables.h and event_object_movement.c; the Eirika sprite sources (eirika_*.png/.4bpp, eirika.pal, tools/leg4_eirika_overworld.py, tools/leg5_eirika_vehicles.py) are kept but no longer used. Ephraim/other-character overworld sprite work for the player is dropped (tools/leg6_npc_sprites.py is an unfinished, unused draft). Story map NPC stand-in sprites unchanged. Eirika remains the Pokemon, portrait and story character. ROM builds/Pokemon FireRed Eirika Leg6-LeafSprites.gba, IPS patches/FireRed_Eirika_Leg6_LeafSprites.ips (applies to vanilla BPRE).
- Done (agent 4, step 3): furniture for the six story maps. `tools/leg6_props.py` lists FE8 backdrop crops (pillars, window panels, lattice screens, rubble, broken columns) pasted into the deeper floor of each map by `tools/leg4_story_tilesets.py` (PROPS=0 turns it off), with collision on the lower half via `tools/leg5_story_map_objects.py`, which also moves any NPC that landed on a blocked cell. Still within the 384 tile limit (near duplicates merged, so some blockiness). Not yet viewed in the emulator. ROM builds/Pokemon FireRed Eirika Leg6-Furniture.gba, IPS patches/FireRed_Eirika_Leg6_Furniture.ips.
- Step 4/5 (agent 4): no further open build items remained beyond owner-dropped overworld sprites; NPC stand-in sprites stay. Source of truth now decomp_full_v5.tar.gz (v4 and older untouched; copy data/mb_*.gba from pret before make). Check run on builds/Pokemon FireRed Eirika Leg6-Furniture.gba: chapters 0-22 headless, 22 pass; chapter 18 hung once in a full sweep (Gengar Destiny Bond took Eirika, test move rotation) and passed on two reruns plus on Leg6-StatFlashFix, so it is test flakiness. All six story maps load and show the new props (docs/img/story_maps_furniture.png, temporary start-map builds, not shipped). Ally lines read in chapters.json and overflow scan (173 segments, same as the earlier baseline pattern, only "'s" 37-glyph lines new) but not seen on screen in game.

## Update 2026-10-16 (agent 5, grok, session 1)
- Done: ending. The final chapter (22) now plays a 10 line epilogue with portraits (Eirika, the 8 allies, Eirika) from the new `epilogue` field in story/chapters.json (supported by tools/leg3_story.py), then a "THE SACRED STONES / THE END / Thank you for playing." screen after a fade, then the normal return to Pallet Town (guide then says the war is over). Epilogue lines are my own invention. The ROM credits (DoCredits) were not used because they end in a soft reset and show Pokemon credits. ROM builds/Pokemon FireRed Eirika Leg7-Epilogue.gba, patches/FireRed_Eirika_Leg7_Epilogue.ips, source decomp_full_v6.tar.gz (v5 and older untouched).
- Verified: a temp ROM (chapter 22 battle removed, not shipped) ran the epilogue headless, chapter counter advanced, portraits and text boxes seen on screen (Eirika, Tana, Duessel screenshots). The shipped ROM chapter 22 test hangs in the Gengar Destiny Bond battle (same on Leg6-Furniture, so a test artifact, not new).
- Player overworld sprites remain Leaf vanilla.
- Open: no party/deploy screen model specified; ally lines mid-battle not viewed in a full playthrough; chapter 22 headless test needs a Ghost-safe party.

## Update 2026-10-16 (agent 6, grok, session 1): verification and donor maps
- Verification (ROM Leg7-Epilogue, headless mGBA, real flow): chapter 22 now runs to the end. The test driver (tools/chapter_test.py with DUO=1) copies the lead into a second party slot and, when the party menu appears after Destiny Bond, moves the cursor to that mon, so the party survives. Chapter 22 reaches the epilogue (10 portrait lines), then "THE SACRED STONES / THE END / Thank you for playing." on black, then Pallet Town (docs/img/leg7_the_end.png). The THE END screen is a plain text box on a black screen, readable, not a designed title card.
- New tool tools/full_run.py: a real-flow capture, boots the ROM, walks bedroom to Pallet Town, talks to the guide and plays each chapter through (arrival script, story map, dialogue, battle), saving every distinct screen. Chapters 0 to 16 pass in it with all text and portraits readable. Seen in play: ally lines with portraits, double battles with partner mons, chapter title cards.
- Defect fixed: the story maps showed donor map names in the popup (SILPH CO. 11F on the Renais map). Popup is now off on all six story maps.
- Owner rules applied: (1) props cropped from FE8 backdrops are retired (tools/leg6_props.py PROPS is now empty, the old list is kept as PROPS_OLD); (2) Fort Rigwald and the Grado Throne Room now use existing FireRed interiors (Pokemon League Bruno's room and Champion's room layouts with gTileset_PokemonLeague) via tools/leg7_donor_maps.py. Their NPCs and treasure moved to walkable cells, backdrop signs removed, arrival and exit warp at (6,10) for the Fort and (6,18) for the Throne Room (chapter scripts regenerated so arrival matches). The other four maps keep clean FE8 floors/backdrops without props. Checked in emulator for chapters 8 and 21 (docs/img/leg8_fort_rigwald_donor.png, leg8_grado_throne_donor.png). ROM builds/Pokemon FireRed Eirika Leg8-DonorMaps.gba, IPS patches/FireRed_Eirika_Leg8_DonorMaps.ips, source decomp_full_v7.tar.gz (older tarballs untouched). Rebuild order: leg4_story_tilesets.py (PROPS=0), leg5_story_map_objects.py, leg7_donor_maps.py, then SCRIPTS_ONLY=1 leg3_story.py.
- Player overworld sprites remain Leaf vanilla.

## Update 2026-10-16 (agent 6, grok, indoor tiling)
- Done: rule driven indoor autotiler `tools/indoor_tiling.py` with rules in `docs/INDOOR_TILING.md`. It mirrors the outdoor tools (lawn_rules, rock_rules, edge_rules, retree in Pokemon-War-and-Murder): cardinal neighbours pick edge blocks, diagonal-only neighbours pick convex corners, two cardinals concave corners, a repeat table (floor accent never touches itself), unknown neighbourhoods are errors, and validate() checks wall ends, door access (flood fill), clear cells in front of doors and wall objects, primary-only palettes.
- Test room 15x16 mixing FE8 (stone floor and wall pieces from graphics/bg of the FE8 decomp, found by seam search, no furniture cropped) and FireRed building tileset objects (rug, table, chairs, plants, door mat, window, shelf, cabinet, fridge). Trick: FireRed furniture keeps its top layer and only the parquet quadrants of its bottom layer are replaced by FE8 floor quadrants. Floor shading near walls is a palette swap per 8x8 quadrant (EDGE and CONVEX tables).
- Images: docs/img/indoor_tiling_test.png, docs/img/indoor_tiling_test_sources.png (which tiles are FireRed, FE8 or both), docs/img/indoor_tiling_test_emulator.png (mGBA, temporary start-map build from decomp_full_v6, not shipped). Tileset and map in workdata/indoor_tiling_test/.
- Not applied to the six story maps yet. Gaps: no inner rug corner or one wide rug block in FireRed, no wall end corner blocks.
- Follow-up (agent 6): in the emulator the Black Temple (chapter 22) FE8 backdrop rendered as noisy static, so it now also uses an existing FireRed interior, the Pokemon Tower 6F layout (tools/leg7_donor_maps.py), arrival and exit at (11,16). Compile check only, not run (owner stopped testing). ROM builds/Pokemon FireRed Eirika Leg9-BlackTempleDonor.gba, IPS patches/FireRed_Eirika_Leg9_BlackTempleDonor.ips, source decomp_full_v8.tar.gz. Test tool note: tools/full_run.py chapters 0-21 passed in real flow; chapter 22 in full_run stalls on the optional "change POKEMON?" prompt (driver issue, the earlier chapter_test.py DUO=1 run reached THE END). Testing stopped by owner order.

## Update 2026-10-16 (agent 7, grok, Leg9 build-only batch)
- Step 1: the four story maps Renais Castle, Frelia Castle, Jehanna Hall and Black Temple are now built by `tools/indoor_tiling.py` through `tools/leg9_indoor_maps.py`: FE8 stone floor and wall, FireRed furniture lifted onto the FE8 floor (no cropping). NPCs, treasure and signs moved onto valid cells, exit warp on the door mat. Fort Rigwald and Grado Throne Room stay on the FireRed donor interiors. Black Temple conflict: agent 6 switched it to the Pokemon Tower 6F donor in parallel (decomp_full_v8, ROM Leg9-BlackTempleDonor); the owner's order for this batch named Black Temple for the autotiler, so Leg9-IndoorMaps and Leg9-TextPass use the autotiled Black Temple (dark FE8 walls, altar table). If the autotiled temple looks bad in the emulator, rerun leg7_donor_maps.py (with the Black Temple donor entry) after leg9, or use the v8 ROM.
- Step 2: autotiler gets wall end corner blocks (palette 10 shade on the outer quadrant column of FE8 wall ends) and an irregular floor (hashed, non touching accents, mirrored floorA variants via flip bits; selftest asserts both). Docs updated.
- Step 3: real Pokedex text for Eirika and the 8 allies (plain FE8 flavor, 3 lines each, <= 36 glyphs); epilogue and ally lines tidied (L'Arachel is Rausten's hero, not Rhoden; Duessel is the Silver Axe; Ross and Garcia are not party members; contractions removed in recruit lines). `tools/check_overflow.py` shows no story text over the limit.
- Build only: compile success is the only check. Nothing here was run in an emulator. ROMs `builds/Pokemon FireRed Eirika Leg9-IndoorMaps.gba` (steps 1 and 2) and `builds/Pokemon FireRed Eirika Leg9-TextPass.gba` (steps 1 to 3), IPS `patches/FireRed_Eirika_Leg9_IndoorMaps.ips` and `patches/FireRed_Eirika_Leg9_TextPass.ips`, source `decomp_full_v9.tar.gz`.
- Open: view the four rooms in the emulator when testing is allowed again; check that the arrival walk up from (7,15) to (7,11) leaves each room's carpet and NPCs as designed.

## Leg10 (agent 8, build only, compile check only, no emulator run)
- Step 1: arrival fix is now in the generator. `tools/leg3_story.py` `mapinfo()` returns (7,15) for the four autotiled maps (Renais Castle, Frelia Castle, Jehanna Hall, Black Temple) whose exit warp sits on the door mat (7,14). Regenerating `story_chapters.inc` with `SCRIPTS_ONLY=1` now keeps arrival at (7,15) so the 4 step walk up lands on (7,11). Checked by regenerating: the output matches the hand patched file except for step 2. No ROM change, so no separate ROM (identical to Leg9-TextPass).
- Step 2: designed THE END title card. `tools/leg10_the_end_card.py` renders a 240x160 card (navy banded sky, stars, gold double border with corner diamonds, gold serif "THE SACRED STONES" and "THE END" with dark outline and shadow, ornament rules, "Thank you for playing.") and converts it to 225 deduplicated BG tiles, a 32x32 tilemap and a 16 colour palette. New `src/story_the_end.c` (`special ShowStoryTheEnd`) shows it on BG0 with a fade in, holds until A or B (after 1 second) or 12 seconds, fades out and returns to the field. `leg3_story.py` calls it in place of the old text box. Design preview: `docs/img/the_end_card.png`. Not run in an emulator, compile check only. ROM `builds/Pokemon FireRed Eirika Leg10-TheEndCard.gba`, IPS `patches/FireRed_Eirika_Leg10_TheEndCard.ips`, source `decomp_full_v10.tar.gz` (all older tarballs untouched). Unverified: palette fade timing and the return to the field after the special.
- Step 3 (docs, no ROM change): `docs/DEPLOY_AND_PARTY.md` (party model, partner slots, chapter table generated from story/chapters.json, no deploy screen), `docs/ARTIFACTS.md` generated by new `tools/list_artifacts.py` (every ROM, IPS and tarball with size, SHA-1 and whether it is noted; older ROMs without an IPS are listed as such), STORY_PLAN.md status section, stale en dash removed from docs/GRAPHICS.md. Text pass: no em or en dashes remain in the notes or chapters.json. ROM is identical to Leg10-TheEndCard.
- Live open list (all need an emulator or an owner decision, so not built here): view the four autotiled rooms and check the arrival walk (7,15) to (7,11); view the THE END card on hardware or in mGBA and confirm the fade and return to Pallet Town; read ally lines on screen in a full run; stat-flash fix in a real battle; Black Temple is a Pokemon Tower 6F donor layout in Leg9-BlackTempleDonor but the later Leg9 autotiled temple replaced it (unviewed); NPC sprites on story maps are FireRed stand-ins; Ephraim and other FE8 overworld sprites are not made (player sprites stay Leaf vanilla by owner order).

## Leg11 (wall fix, build only, compile checked)
- Owner order: one wall style per room, wall width must equal floor width, audit all story maps. Done in tools/indoor_tiling.py validate() and tools/leg9_indoor_maps.py. Details in docs/INDOOR_TILING.md ("Wall rules").
- ROM `builds/Pokemon FireRed Eirika Leg11-WallFix.gba`, IPS `patches/FireRed_Eirika_Leg11_WallFix.ips`, source tree `decomp_full_v11.tar.gz`. Offline render: `docs/img/indoor_walls_fixed.png`. Not run in an emulator.

## Update 2026-10-16 (Leg12, story depth, build only)
- Audit in `docs/STORY_GAPS.md`. Built: skirmish battle first in every chapter, chapter 5x, per chapter partner and enemy clones (fixes last-use level scaling), doubles for chapters 17, 21, 21x, 4 extra scene lines per chapter, Ephraim cameos, ally lines for chapters 8 to 13, Frelia guard sprite. Generator `tools/leg3_story.py` now resolves battles and clones (chapter labels via `label`); content was added by `tools/leg12_expand_story.py`, `leg12_expand_story2.py`, `leg12_expand_story3.py` (one time, already applied to story/chapters.json). Audit tool `tools/story_audit.py`.
- Compile check only, nothing run. ROM `builds/Pokemon FireRed Eirika Leg12-StoryDepth.gba`, IPS `patches/FireRed_Eirika_Leg12_StoryDepth.ips` (round trip verified), source `decomp_full_v12.tar.gz` (carries no mb_*.gba; copy from pret before make). Overflow scan unchanged (173, same baseline).
- Not built: optional dungeons (Tower of Valni, Lagdou Ruins, Melkaen Coast). Open (emulator or owner): see the Leg10 live open list.


## Emulator verification (2026-10-16)
- Ran the headless harness on Leg12-StoryDepth. Full report: `docs/VERIFY_REPORT.md`, images `docs/img/verify_*.png`. Results: story maps PASS, ally and cameo text PASS, stat flash PASS, chapter sweep 0 to 23 (including 5x and 21x) PASS with no crashes, THE END card FAIL in Leg12 (missing BG tilemap buffer in `src/story_the_end.c`) and fixed in `builds/Pokemon FireRed Eirika Leg14-EndCardFix.gba`, IPS `patches/FireRed_Eirika_Leg14_EndCardFix.ips`, source `decomp_full_v14.tar.gz`. Black Temple look FAIL (pale, washed out palette in game), not fixed. Harness note: `tools/chapter_test.py` now takes `SB1PTR` (default 0x03005028 for Leg12 and later).

- Leg15 (final release). Black Temple fix: the washed out look was not a palette bug. The map still had the Pokemon Tower donor weather `WEATHER_FOG_HORIZONTAL`, a fog overlay. Set to `WEATHER_NONE` in `tools/leg9_indoor_maps.py` (a one byte ROM change). Verified in the headless emulator: `docs/img/verify_black_temple_fixed.png` shows brick wall, one wall style, wall width equals floor width, no fog. Autotiled temple kept (no donor switch needed). Chapter 13 flash rectangle left as is (not trivial). Release: `patches/PokemblemTheSacredStones.ips` applied to vanilla FireRed gives `release/PokemblemTheSacredStones.gba`, SHA-1 7adcc1dd4a928d17b18eed1ae6271ed6300e5eac, byte-identical to the built Leg15 ROM, checked with two patchers. Boots to the player's room (`docs/img/verify_release_boot_room.png`) and shows the new Black Temple (`docs/img/verify_release_black_temple.png`). Source `decomp_full_v15.tar.gz`.

## Leg16: Eirika overworld sprite (2026-10-17)
- Player walk/run sprite is now the owner approved recolor (hat to blue hair, gold/red/white/red bands). Source: `graphics/object_events/pics/people/eirika_walk.png` plus `palettes/eirika_walk.pal` and `eirika_walk_reflection.pal`, rule added to `spritesheet_rules.mk`, new palette tags in `src/event_object_movement.c`. Bike, surf, fish and item sprites stay Leaf vanilla on the PLAYER_GREEN palette.
- The sheet had 16 opaque colors (GBA limit is 15 plus transparent): brown (106,41,41) merged into (123,65,65).
- ROM `builds/Pokemon FireRed Eirika Leg16-EirikaSprite.gba`, SHA-1 `b788d9d7eee69038f6726d0dd6f37d8ab834b701`, source `decomp_full_v16.tar.gz`. Release files regenerated; the previous ones are `patches/archive/PokemblemTheSacredStones_pre_sprite.ips` and `release/archive/PokemblemTheSacredStones_pre_sprite.gba`.
- Verified headless: boots to the player's room, stand and walk in four directions (`docs/img/verify_eirika_sprite_montage.png`), NPCs fine. Surf and bike not exercised live.

## Leg17: healer and vendor NPCs (2026-10-17)
- Each of the six story maps now has a healer (OBJ_EVENT_GFX_NURSE stand-in for a cleric; yes/no, `special HealPlayerParty`, MUS_HEAL fanfare) and vendors (OBJ_EVENT_GFX_CLERK) that open the vanilla pokemart lists by referencing the global vanilla labels, so the stock is an exact copy. Code: `SERVICES` in `tools/leg5_story_map_objects.py`; placement for the donor and autotiled maps in `tools/leg7_donor_maps.py` and `tools/leg9_indoor_maps.py` (auto placement keeps all floor cells reachable and the entry lane clear). leg7 no longer switches Black Temple to the Pokemon Tower donor (leg9 undid that anyway; run order leg5, leg7, leg9, leg3 SCRIPTS_ONLY=1 now works).
- Stocks in progression order: Renais Castle: Viridian, Pewter. Frelia Castle: Cerulean, Vermilion. Fort Rigwald: Lavender, Celadon 2F items. Jehanna Hall: Fuchsia, and one Grand Merchant with the Celadon big market (asks yes/no for 5F vitamins HP Up, Protein, Iron, Calcium, Zinc, Carbos; 5F X items; 2F TMs; 4F stones). Grado Throne Room: Saffron, Cinnabar. Black Temple: Indigo Plateau, Seven Island. Not used: Two, Three, Four, Six Island, Trainer Tower. Vanilla maps used by chapters (Route 1, Pewter City and so on) were not touched.
- ROM `builds/Pokemon FireRed Eirika Leg17-HealerVendors.gba`, source `decomp_full_v17.tar.gz`, release IPS and GBA regenerated (previous ones in patches/archive and release/archive as `_pre_healervendors`). Verified headless: `tools/verify_rooms.py` (env WARP_OFF=0x4e7768 WARP2=1) shows all NPCs on all six maps (`docs/img/verify_leg17_story_maps.png`); `tools/verify_services.py` on Jehanna Hall: healer restored HP 1 to full, Fuchsia vendor opens BUY/SELL menu (`docs/img/verify_leg17_heal_mart.png`). The Celadon yes/no chain was compiled but its menus were not exercised live.

## Leg18: playable flow (2026-10-17, IN PROGRESS, checkpoint 1)
- ROOT CAUSE of the starter soft lock: Eirika is created at new game (`CreateStarterEirika`), but the vanilla Oak gate (VAR_MAP_SCENE_PALLET_TOWN_OAK = 0, Oak stops the player at the Pallet Town grass and leads to the lab) and the lab starter scene were still active. The starter ball in the lab says "EIRIKA already has her partner", so the choice could never complete.
- FIX (done): `src/new_game.c` now sets OAK=3, LAB=7, PLAYERS_HOUSE_2F=1, FLAG_SYS_POKEDEX_GET, VAR_STORY_CHAPTER=0, VAR_STORY_PENDING=1 and warps a new game straight into Renais Castle (7,15) instead of the bedroom. Pallet Town guide NPC removed (generator).
- FLOW (done): see docs/STORY_FLOW.md. Chapter win -> warp to hub camp (VAR_STORY_PENDING=2, `Story_Camp`) -> door tile coord event `EventScript_StoryDepart` (yes/no) -> next chapter map entry cutscene. `src/overworld.c` passes pending into VAR_0x8004. Whiteout returns to the hub camp (`src/heal_location.c` sStoryHubs, `data/scripts/white_out.inc` Story_Retreat). `special StoryLevelCatchUp` (script_pokemon_util.c, pokemon.c StoryRaiseMonLevel) raises the party to chapter level +2 at each chapter start (no grinding exists; an unaided L5 Eirika lost chapter 0). Generator: tools/leg3_story.py (idempotent, also patches the six story map.json files and Pallet Town).
- Tree: decomp_full_v18.tar.gz. ROM builds/Pokemon FireRed Eirika Leg18-PlayableFlow.gba, IPS patches/FireRed_Eirika_Leg18_PlayableFlow.ips. Release files NOT yet rebuilt.
- Playthrough harness: `python3 tools/full_playthrough.py ROM OUTDIR` (real presses for intro, scenes, walking to the camp door; test aid buffs HP/stats, NOBUFF=1 for unaided; START_CH=n debugging jump; BUFFLEVEL=0 default). `tools/newgame_run.py` for just the intro. Results so far: new game goes to chapter 0, chapters 0 to 20 passed in an earlier buffed run (before the level catch-up); a later run stalled at chapter 2 only because the harness buff wrote Lv100 into the party level field (now BUFFLEVEL=0).
- NEXT: run `rm -rf /workspace/L18/pt; python3 tools/full_playthrough.py <rom copy> /workspace/L18/pt` (about 6 min, run in background, poll the log), fix blockers, then write docs/PLAYTHROUGH_REPORT.md with screenshots in docs/img/, rebuild release (tools/make_ips.py, tools/apply_ips.py, SHA-1 check, archive previous release as _pre_playableflow).

### Leg18 checkpoint 2 (2026-10-17)
- Buffed playthrough from a fresh new game with the Leg18 ROM: chapters idx 0 to 14 PASS, idx 15 (Celadon, label 14 "Queen of White Dunes" is idx 15) STUCK, under investigation (screens in /workspace/L18/pt, not yet in docs/img). Harness fixes: tools/full_playthrough.py now taps B,B,UP,LEFT every 9 loops (backs out of the battle party/summary screens and puts the battle cursor on FIGHT). Next: look at /workspace/L18/pt/ch15_*.png, fix, continue with START_CH=15 python3 tools/full_playthrough.py ROMCOPY OUT.
