# Story gaps audit (Leg12, 2026-10-16)

Audit of `story/chapters.json` (as of Leg11) against `docs/FE8_CHAPTERS.md` and `docs/STORY_PLAN.md`. Build only, compile check only, nothing run in an emulator. Tool: `tools/story_audit.py`.

## Findings (before Leg12)
| # | Gap | Priority | Status |
|---|---|---|---|
| 1 | Every chapter had one battle and a one-paragraph scene (thin). No skirmish before the boss. | high | Built: a skirmish battle first in every chapter (fresh trainers by FE8 enemy theme), the existing boss battle last, mid line between them |
| 2 | Chapter 5x (Unbroken Heart) was in the plan and never built. The story had 23 chapters, the plan says 24. | high | Built: chapter 5x on the Renais Castle map, skirmish plus Zonta boss, labelled "CHAPTER 5x" (display labels are now per chapter, so FE8 numbers are kept) |
| 3 | Partner trainers were reused across chapters (Blaine 5 to 8, Sabrina, Agatha, Brock, Erika and others), and `plan` is keyed by trainer, so every use got the level of the LAST chapter using it. Early partners were over-levelled. Same for repeated enemy trainers. | high | Built: reuse now gets a clone (unused RS trainer slot with the source trainer's class, pic and name, own party), so each chapter has its own party at its own level. 20 clones |
| 4 | Chapters 17 (Lyon), 21 (Lyon possessed) and 21x (Fomortiis) were single battles with no partner. | high | Built: double battles with an AI partner (Misty, Sabrina, Lt. Surge slots) and a second enemy trainer. Fomortiis marked as a boss |
| 5 | Scene text was one line before and one after. Seth, Ross, Garcia, Colm, Rennac, Gerik, Tethys, Amelia, Syrene and the villains had no lines. | medium | Built: 2 lines before and 2 lines after in every chapter (`scene_before`, `scene_after`), cameos as plain text boxes with the name in the text. Only Eirika and the 8 allies have a portrait (they are the only species with FE8 portraits) |
| 6 | Ephraim appeared only in two lines (prologue, chapter 1). | medium | Built: Ephraim cameos in chapters 2, 8 (the split), 10, 13, 15 (letters), 18 (reunion), 19, 20, 21, 21x and the epilogue. The Ephraim route battles stay out of scope (STORY_PLAN decision 1) |
| 7 | Allies had no lines in chapters 8 to 13. | medium | Built: `ally_talk` lines for labels 8 to 13. All 8 allies now speak, and no ally speaks before they are recruited (checked by `tools/story_audit.py`) |
| 8 | Frelia Castle guards used the plain MAN sprite. | low | Fixed: POLICEMAN stand-in (closest FireRed guard sprite). Other stand-ins checked and kept: Grado guards ROCKET_M, temple cultists CHANNELER, Jehanna sage CHANNELER, Fort Rigwald scout HIKER |
| 9 | Tower of Valni, Lagdou Ruins, Melkaen Coast optional dungeons (STORY_PLAN decision 8). | low | NOT built. Needs new multi floor maps and encounter tables; no FE8 art question, but it is a large map build that is better done as its own leg |
| 10 | Ephraim route chapters 9b to 21b. | n/a | Out of scope by decision 1 (summary lines only) |
| 11 | Ross, Garcia, Colm, Rennac, Gerik, Tethys, Marisa, Amelia and Syrene are recruits in FE8 but are not among the 8 playable ally species. | n/a | Kept as dialogue cameos (decision 2 limits playable allies to 8) |
| 12 | Open items that need an emulator or owner choice: view the four autotiled rooms and arrival walk, THE END card, ally lines on screen, stat flash fix in battle, Black Temple choice (autotiled vs Tower 6F donor). | n/a | Not built, by the no-testing rule. Nothing buildable remains on that list |

## Per chapter summary after Leg12
Run `python3 tools/story_audit.py story/chapters.json` for the table. Every chapter: map, 2 battles (skirmish, then boss; chapters 3 on are doubles with a partner), 4 extra scene lines, a mid line, an after line, a reward, and an ally line from chapter 6 on (chapters 0 to 5x have none because no ally has joined, except Joshua from chapter 5). Recruit scenes are in chapters 5, 9, 10, 11, 12, 13. Ending: chapter 21x epilogue (11 lines including Ephraim) then the THE END card.

## Known limits
- Skirmish enemies are vanilla FireRed trainers re-partied by theme (see `docs/STORY_PLAN.md` enemy class table).
- Cameo lines have no portrait for non-playable characters.
- Level pacing was set by the generator table `LV` (24 entries) and not checked in play.
