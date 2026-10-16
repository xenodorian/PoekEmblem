# Current Work: Fire Emblem: The Sacred Stones story in Pokemon FireRed

Rules: work only on `main`, never create branches. ROMs are copyrighted and gitignored, never commit them. Extracted FE8 art is also kept out of the repo (personal use only, not for distribution).

Base ROM: `Pokemon - FireRed Version (USA).gba`, BPRE, SHA-1 `41cb23d8dccc8ebd7c649cd8fbb58eeace6e2fdc`. Story source ROM: `Fire Emblem - The Sacred Stones (USA, Australia).gba`, BE8E.

Status as of 2026-10-16: planning plus feasibility prototypes. No ROM has been patched and nothing in this list has been executed in the repo yet. All prototype work lives in session scratch space and is listed under "What exists today".

## Leg 1 progress (2026-10-16)
Built from a copy of the FireRed decomp (`/home/user/pret/pokefirered_leg1`, session only). Source changes are in `patches/leg1/leg1_src.diff` (code only). The art swaps use FE8 art, so they and the IPS built from them are not in the repo. The IPS was made locally as `FireRed_Eirika_Leg1.ips` (applies to vanilla BPRE, verified byte-identical to the built ROM).
- Done: NEW GAME skips the controls guide, Pikachu intro, Oak's speech and all naming. The player is female and named EIRIKA, the rival is named LYON, and the game starts in the player's room (checked in the emulator).
- Done: Eirika art replaces Leaf in the trainer front pic (trainer card, link and other uses), Oak speech pic (no longer shown), battle back pic and region map icon. The overworld sprites are unchanged.
- Done: species EIRIKA uses the old "?" slot 276 (`SPECIES_EIRIKA`). Scizor's base stats, types (Bug/Steel), ability (Swarm), exp, EV yield, TM/HM and tutor compatibility and cry. Gender is fixed female. Front, back and icon are the Eirika portrait crop. The learnset is Scizor's with these changes: Metal Claw (was 26), Slash (was 31) and Fury Cutter (was 46) are moved, and the 11 requested moves are placed at levels 7 Scratch, 9 Fury Cutter, 12 Fury Attack, 14 Cut, 17 Metal Claw, 19 Razor Leaf, 22 Vice Grip, 25 Slash, 28 Steel Wing, 31 Razor Wind, 34 Cross Chop. Scizor's own Pursuit 11, False Swipe 16, Agility 21 and Swords Dance 36 are unchanged.
- Done: every new game gives the player a level 5 Eirika in party slot 1 with all IVs 31 (verified in memory), marked seen and caught, and sets the has-Pokemon flag.
- Checked in emulator: room loads, party screen and summary show Eirika with the portrait icon, and a test battle uses her back sprite.
- Not done: Eirika attack animation in battle (next), Oak's lab starter and the "Oak stops you in the grass" scripts still expect a starter, the rival's art, overworld sprites, the "Met in CELADON DEPT." origin text, Pokedex entry and number for Eirika.

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

## Proposals still waiting on your approval
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

## What exists today (all outside the repo, in session scratch)
Scripts: `fe8_portrait.py` (portrait assembler), `make_test_sprite.py` (back sprite builder with the top-first crop), `banim_render.py` (FE8 animation renderer), `shot.c` (headless mGBA driver), `extract_fx.py` (effect isolation, not needed going forward), `mockups.py`. Outputs: `playable_allies/` (10 folders with back sprites and talk portraits), `back_sprites/` (90 portraits, of which only the allies are needed), `fe8_deployment_counts.csv`, and the composited demo GIFs. These live in a session scratch folder that is not saved with the repo, so the scripts must be committed to `tools/` before the session ends (see tasks).

## Leg 1: Cast swap
### Proposed master list (draft, not approved)
| FE8 character | Proposed FireRed character | Note |
|---|---|---|
| Eirika | Leaf (female player) | From request |
| Ephraim | Red (male player) | From request |
| Lyon | Rival (renamed) | From request |
| Seth | Brock | Proposal |
| Franz | Misty | Proposal |
| Gilliam | Lt. Surge | Proposal |
| Vanessa | Erika | Proposal |
| Moulder | Professor Oak | Proposal |
| Garcia | Koga | Proposal |
| Neimi | Daisy | Proposal |
| Cormag | Lance | Proposal |
| Natasha | Nurse Joy | Proposal |
| Lute | Sabrina | Proposal |
| Joshua | Blaine | Proposal, check vibe |
| Tana | Bill | Proposal, check vibe |
| L'Arachel | Lorelei | Proposal |
| Dozla | Bruno | Proposal |
| Myrrh | Agatha | Proposal |
| Innes | Giovanni | Proposal, check vibe |

Note: the allies in this table are also Leg 2 Pokemon. Reconcile this so each ally has one identity. The remaining FE8 names (Ross, Colm, Artur, Pablo, Igrene, Tethys, Marisa, Amelia, Saleh, Ismaire, Syrene, Orson, Caellach, Breguet, Knoll, Ewan, Glen, Forde, enemy generals) are not mapped. FireRed has 107 trainer classes available for reuse; each mapping must check that the class and sprite exist in the build.

## Leg 2: Friendly NPCs as party Pokemon
Species and moves proposal (not approved, moves unverified against Gen 3 learnsets):

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

## Open questions
1. Party model. Recommendation (not approved): a roster of up to 18 allies stored in extra storage plus 6 deployed, swapped on a deploy screen like FE8's prep screen. A true 18-slot party needs an engine-wide rewrite and a save restructure (1,200 bytes more than the 152 free). A smaller option is 8 deployed, which needs the battle party order packing widened.
2. Which of the other 23 playable FE8 characters, if any, become playable Pokemon.
3. Real Whirlwind (wind lines that blow the enemy off screen) or the Wing Attack twin-tornado effect?
4. Move-to-animation mapping: which moves use which FE8 animation (close, critical and ranged variants exist). Fly could be split into two turns.
5. Where is the "Cathleen" example in the War and Murder repo?
6. Gen 1 species only, or add species?
7. Timing unit of the FE8 animation scripts (assumed 1/60 s).

## Task list (nothing started)
1. Commit the prototype scripts (`fe8_portrait.py`, `make_test_sprite.py`, `banim_render.py`, `shot.c`) to `tools/` on `main`, art excluded.
2. Port the War and Murder tile tools to vanilla FireRed. Re-dump offsets and confirm `tilecheck.py` passes on the base ROM.
3. Leg 1: approve the master cast list, then skip the intro and naming screens, set Eirika, Ephraim and Lyon, and apply the renames.
4. Leg 1 test: confirm names and the skipped intro in mGBA with the headless harness.
5. Leg 2: decide species, moves and the party model. Verify moves against Gen 3 learnsets.
6. Leg 2: add the 8 ally species with portrait back sprites, palettes, icons and cries.
7. Leg 2: build the FE8 attack animation system (hook `LaunchBattleAnimation`, frame renderer to compact data, playback task, palette and tile budgeting, effect timing).
8. Leg 2: build the roster and deploy screen once the party model is approved.
9. Leg 2: add recruitment scripts for each ally.
10. Leg 3: write the chapter outline and the node-to-map assignment.
11. Leg 3: map enemy classes to trainer classes and Pokemon (about 70 classes, 151 native species) and plan boss fights for about 33 unique IDs.
12. Leg 3: build the custom maps, then test the full flow.
