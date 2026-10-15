# Current Work: Fire Emblem: The Sacred Stones story in Pokemon FireRed

Branch: `main` (no other branches). Base ROM: `Pokemon - FireRed Version (USA).gba`, BPRE, SHA-1 `41cb23d8dccc8ebd7c649cd8fbb58eeace6e2fdc`. Story source ROM: `Fire Emblem - The Sacred Stones (USA, Australia).gba`, BE8E. Both ROMs are gitignored and are never committed.

Status as of 2026-10-15: planning only. No ROM has been patched yet.

## Goal
Recreate the story of FE8 (Sacred Stones) inside FireRed, in three legs.

## Reference sources
- FireRed decomp (pret): `/home/user/pret/pokefirered` (read-only clone, shallow).
- FE8 decomp (FireEmblemUniverse): `/home/user/fireemblemuniverse/fireemblem8u` (read-only clone, shallow).
- Tiling and map tools: `/home/user/xenodorian/pokemon-war-and-murder` (read-only clone, shallow). Key files: `tools/tilecheck.py` (metatile and palette validator), `tools/army_tiles.py`, `tools/rock_rules.py`, `tools/lawn_rules.py`, `tools/species_add.py` (adds a new species with front and back art), `tools/story_party.py` (party and NPC insertion), `tools/story_species.py`, `tools/mapinfo.py`, `tools/dumpmap.py`, `tools/build_full.sh`, `docs/STORY_PLAN.md` (story design format to copy).
- Local tools installed: mGBA 0.10.2 (`/usr/games/mgba`), ghex, hexedit, arm-none-eabi binutils and gcc, python3 Pillow.

### Known constraints found in the reference repo
- Its tools were written for a different base ROM (Pokemon Outlaw, build `f4046af2`, 16,777,240 bytes). Its paths are hard-coded to `/home/claude/work`. Our base is vanilla FireRed, so the tools need porting. Expect offsets to differ.
- Its tile and palette checks (`tilecheck.py`) and its metatile logic apply to any FireRed-engine ROM and are reusable once offsets are re-dumped.

## FE8 facts verified from the FE8 decomp (`src/data_characters.c`)
Verified: each name below exists as `CHARACTER_*` in the decomp, and the class, affinity, base level and weapon ranks were read from the file.

| FE8 unit | Default class | Affinity | Base lvl | Weapon ranks (A-E) |
|---|---|---|---|---|
| Innes | Sniper | Ice | 1 | Bow A |
| Tana | Pegasus Knight | Wind | 4 | Lance D |
| L'Arachel | Troubadour | Light | 3 | Staff D |
| Dozla | Berserker | Thunder | 1 | Axe B |
| Joshua | Myrmidon | Wind | 5 | Sword C |
| Duessel | Great Knight | Anima | 8 | Sword A, Lance A, Axe A |
| Cormag | Wyvern Rider | Fire | 9 | Lance C |
| Myrrh | Manakete | Wind | 1 | none |
| Eirika | Eirika Lord | Light | 1 | Sword E |
| Ephraim | Ephraim Lord | Fire | 4 | Lance D |

Not yet verified: signature skills per unit, and the story beats. Those come from the FE8 decomp `data/` and `src/` skill and event files. Do not state them as fact until read.

## Leg 1: Cast swap (protagonists and names)

Decisions from the request:
- Skip the intro and naming screens.
- Protagonist: female Leaf (called "Green" in the request). Name: Eirika.
- Male Red (the default male player) is Ephraim, who appears later in the story.
- The rival (default name BLUE in FireRed; the request calls this character Gary) becomes Prince Lyon of Grado.
- Other characters are reused and renamed the same way.

Constraint to decide: FireRed player and rival names are limited to 7 characters. "Lyon" fits. "Prince Lyon of Grado" does not. Proposal: display name "LYON" in the name field and put "Prince of Grado" in dialogue. Needs your approval.

### Proposed master list (draft, not approved)
Core story characters only. Full FE8 roster is 40+ named units, including enemies.

| FE8 character | Proposed FireRed character | Note |
|---|---|---|
| Eirika | Leaf (female player) | Confirmed by request |
| Ephraim | Red (male player) | Confirmed by request |
| Lyon | Rival (renamed) | Confirmed by request |
| Seth | Brock | Proposal |
| Franz | Misty | Proposal |
| Gilliam | Lt. Surge | Proposal |
| Vanessa | Erika | Proposal |
| Moulder | Professor Oak | Proposal |
| Garcia | Koga | Proposal |
| Neimi | Daisy | Proposal |
| Cormag | Lance | Proposal, dragon master fits Wyvern Rider |
| Natasha | Nurse Joy | Proposal |
| Lute | Sabrina | Proposal |
| Joshua | Blaine | Proposal, check vibe |
| Tana | Bill | Proposal, check vibe |
| L'Arachel | Lorelei | Proposal |
| Dozla | Bruno | Proposal |
| Myrrh | Agatha | Proposal |
| Innes | Giovanni | Proposal, check vibe |

Remaining FE8 names (Ross, Colm, Artur, Pablo, Igrene, Tethys, Marisa, Amelia, Saleh, Ismaire, Syrene, Orson, Caellach, Breguet, Knoll, Ewan, Duessel, Glen, Forde, Heath, enemy generals) are not mapped yet. Map them in a later pass after the core list is approved.

FireRed trainer classes available for reuse (from `include/constants/trainers.h`, 107 entries): Leader, Elite Four, Champion, Rival early and late, Team Rocket, Team Aqua, Team Magma, Lass, Youngster, Ruin Maniac, Tamer, Psychic, Sailor, and more. Each proposed mapping must also check that the target trainer class and sprite exist in the FireRed build.

## Leg 2: Friendly NPCs as party Pokemon

Requirement: each NPC becomes a Pokemon that can join the player's party. The Pokemon's battle art is the NPC's FE8 art. Moves are valid for the species and similar to the NPC's FE8 kit.

Proposal (not approved). Species are chosen from Gen 1 (FireRed's native dex). Adding a species needs the approach used in `species_add.py`.

| NPC | FE8 class | Proposed species | Proposed moves (to verify) |
|---|---|---|---|
| Innes | Sniper, bow A | Fearow | Drill Peck, Fury Attack, Focus Energy, Agility |
| Tana | Pegasus Knight, Wind | Pidgeot | Wing Attack, Gust, Quick Attack, Agility |
| L'Arachel | Troubadour, Light staff | Jigglypuff | Sing, Pound, Defense Curl, Disable |
| Dozla | Berserker, Thunder axe | Machamp | Thunderpunch, Karate Chop, Submission, Focus Energy |
| Joshua | Myrmidon, sword C | Scyther | Slash, Wing Attack, Quick Attack, Swords Dance |
| Duessel | Great Knight, Anima | Golem | Rock Throw, Earthquake, Harden, Body Slam |
| Cormag | Wyvern Rider, Fire | Charizard | Flamethrower, Wing Attack, Slash, Fire Spin |
| Myrrh | Manakete, Wind | Dratini | Dragon Rage, Wrap, Agility, Thunder Wave |

Open points:
- Vanilla FireRed has no Gen 2 or Gen 3 species. Moves listed above must be checked against the Gen 3 learnset in pret before use.
- Battle art: FE8 portraits must be converted to Pokemon front and back sprites (64x64, 16-colour). This is the main art task.
- Party insertion: the FireRed party is limited to 6. The NPCs need a script that adds them as Pokemon, not as trainers. Reference: `tools/story_party.py`.

## Leg 3: Story on existing maps

Recreate the FE8 chapter flow on FireRed maps. Build custom maps only where the story needs them. Tile work follows the tools and guides in the reference repo (metatile validation with `tilecheck.py`, lawn and rock rules, and the house and interior graft methods).

Plan:
1. Write the chapter-by-chapter outline in `docs/STORY_PLAN.md`, using the format from the reference repo.
2. Map each chapter to a FireRed town, route, or dungeon. List any chapter that has no FireRed match and needs a custom map.
3. Build custom maps last, once the mapping is approved.

## Task order
1. Port the reference tools to vanilla FireRed (re-dump offsets, confirm `tilecheck.py` passes on the base ROM).
2. Leg 1: approve the master list, then apply name and text changes.
3. Leg 1 test: confirm names and the skipped intro in mGBA.
4. Leg 2: pick species and moves, then convert FE8 art.
5. Leg 2: insert the 8 party NPCs. Test join and battle.
6. Leg 3: write the chapter outline, map chapters to locations, build custom maps as needed.

## Open questions for you
1. Approve the protagonist and rival naming as written above, including the 7-character display name "LYON".
2. Approve or change the core master list (table above).
3. Approve or change the Pokemon species for the 8 NPCs. Gen 1 only, or allow added species?
4. Should the work stay on `main` and be committed there, or should files stay uncommitted until you review?
