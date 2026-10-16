# Deploy and party notes

There is no deploy screen and no 18 member roster. The decision (owner delegation, 2026-10-16) was to model FE8's larger deployments with double battles and an AI partner instead. This file records how the party works so nobody rebuilds it.

## Party model
- The player party is the normal FireRed party of 6. Eirika (species EIRIKA, No.395) is slot 1 from the start at level 5.
- The 8 allies (Innes, Tana, L'Arachel, Dozla, Joshua, Duessel, Cormag, Myrrh, species slots 252 to 259, No.387 to 394) are recruited by `EventScript_Recruit<Name>` in `data/scripts/ally_recruit.inc`, which adds them to the party or the PC when the party is full. Recruit chapters are listed in `story/chapters.json` (`recruits`).
- All other FE8 characters are trainers, partners or NPCs (`docs/LEG1_CAST.md`), not party members.
- After every chapter the party is fully healed and the player gets 500 + 250 x chapter yen.
- Losing a chapter goes through the normal whiteout, then the player can talk to the guide in Pallet Town again. `VAR_STORY_CHAPTER` only advances on a win.

## Partner battles
`special StartPartnerBattle` (see `docs/PARTNER_BATTLES.md`) uses party slots 0 to 2 for the player and fills slots 3 to 5 with the AI partner for the fight, then restores the player's slots 3 to 5. So in a double battle only the first three party members can fight, and the party order sets who leads.

## Chapter table (generated from story/chapters.json)
Partner slot names map to FE8 characters through `docs/LEG1_CAST.md`: BROCK is Seth, BLAINE is Garcia, LT_SURGE is Gilliam, MISTY is Marisa, ERIKA is Vanessa. (`docs/PARTNER_BATTLES.md` says Joshua takes over from chapter 5; the generated scripts use the slots in this table, which is what is built.)

| Chapter | Title | Map | Battle | Partner |
|---|---|---|---|---|
| 0 | The Fall of Renais | STORY_RENAIS_CASTLE | single | none |
| 1 | Escape! | ROUTE1 | single | none |
| 2 | The Protected | STORY_FRELIA_CASTLE | single | none |
| 3 | The Bandits of Borgo | ROUTE3 | double | LEADER_BROCK |
| 4 | Ancient Horrors | VIRIDIAN_FOREST | double | LEADER_BROCK |
| 5 | The Empire's Reach | PEWTER_CITY | double | LEADER_BLAINE |
| 6 | Victims of War | ROUTE2 | double | LEADER_BLAINE |
| 7 | Waterside Renvall | VERMILION_CITY | double | LEADER_BLAINE |
| 8 | It's a Trap! | STORY_FORT_RIGWALD | double | LEADER_BLAINE |
| 9 | Distant Blade | CERULEAN_CITY | double | LEADER_LT_SURGE |
| 10 | Revolt at Carcino | VERMILION_CITY | double | LEADER_MISTY |
| 11 | Creeping Darkness | LAVENDER_TOWN | double | LEADER_ERIKA |
| 12 | Village of Silence | ROUTE9 | double | LEADER_ERIKA |
| 13 | Hamill Canyon | ROCK_TUNNEL_1F | double | LEADER_KOGA |
| 14 | Queen of White Dunes | CELADON_CITY | double | LEADER_SABRINA |
| 15 | Scorched Sand | STORY_JEHANNA_HALL | double | LEADER_SABRINA |
| 16 | Ruled by Madness | FUCHSIA_CITY | double | LEADER_SABRINA |
| 17 | River of Regrets | PALLET_TOWN | single | none |
| 18 | Two Faces of Evil | ROUTE19 | double | ELITE_FOUR_AGATHA |
| 19 | Last Hope | CERULEAN_CAVE_1F | double | ELITE_FOUR_AGATHA |
| 20 | Darkling Woods | VIRIDIAN_FOREST | double | ELITE_FOUR_AGATHA |
| 21 | Sacred Stone | STORY_GRADO_THRONE_ROOM | single | none |
| 22 | Sacred Stone (Final) | STORY_BLACK_TEMPLE | single | none |

## Known limits
- Partner and party lines are not played in game in a full run; see the verification notes in `Current_Work.md`.
- A real deploy or formation screen is not specified by the story plan and is not planned. If the owner wants one, the cheapest option is a script menu (`multichoice`) that reorders the first three party slots before each battle.
- Allies after slot 3 never fight in double battles. Keep the strongest three in the front.
