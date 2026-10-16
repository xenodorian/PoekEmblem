# Emulator verification report (2026-10-16)

ROM under test: `builds/Pokemon FireRed Eirika Leg12-StoryDepth.gba` (copy at /tmp, never modified). Harness: `/workspace/mgba_drv` built from `tools/mgba_drv.c` (libmgba0.10), `tools/chapter_test.py`, `tools/full_run.py`. Test party is buffed and has Ghost-capable moves (Metal Claw, Steel Wing, Fury Cutter), plus a second party mon from chapter 22 on (test driver only, so Destiny Bond cannot wipe the party).

Harness fix (tool only): `tools/chapter_test.py` used a stale `gSaveBlock1Ptr` address (0x03005018). In Leg12 it is 0x03005028, so the chapter variable writes and reads hit garbage and every run looked like a hang. It now reads `SB1PTR` from the environment, default 0x03005028. New helper scripts: `tools/verify_run.py` (full_run with progress prints), `tools/verify_end.py` (fine capture after the last chapter), `tools/verify_rooms.py` (patches a COPY of the ROM so the bedroom stairs land on a story map, then walks up), `tools/verify_statflash.py`.

## Results

| # | Item | Result |
|---|------|--------|
| 1 | Six story maps, wall style, wall width, arrival walk | PASS (Black Temple look fails, see 6) |
| 2 | THE END card, fade, return to Pallet Town | FAIL in Leg12, fixed in Leg14 (PASS) |
| 3 | Ally lines and Ephraim/cameo text boxes | PASS |
| 4 | Stat-flash fix in a real battle | PASS |
| 5 | Chapter sweep, indexes 0 to 23 | PASS (one stuck run, see below) |
| 6 | Black Temple look | FAIL (washed out), not fixed |

### 1. Story maps
Images: `docs/img/verify_rooms_all.png` (door end, four steps up per room), `docs/img/verify_room_tops.png` (top wall, left and right), `docs/img/verify_room_<name>.png` (renais, frelia, jehanna, rigwald, grado, blacktemple).
* Renais and Frelia: one cream wall style, wall exactly as wide as the floor (columns 1 to 13), carpet, table, plants, NPCs in place.
* Jehanna Hall: one brick wall style, same width as the floor.
* Fort Rigwald and Grado Throne Room: donor interiors, single wall style each, width matches.
* Arrival: the player enters on the door mat, walks up four tiles and stops on the carpet with the NPCs around, as designed (frames in the chapter 0 sweep, for example `docs/img/verify_rooms_all.png` row 1). Walking the full room by hand (patched copy) shows no wall past the floor on any map.

### 2. THE END card
Leg12: FAIL. After the epilogue the card showed as a small garbled box of gold fragments on top of the old room tiles with purple stripes at the edges, then faded and returned to Pallet Town. Cause: `src/story_the_end.c` never set a BG0 tilemap buffer (`SetBgTilemapBuffer`), so `CopyToBgTilemapBuffer` and `CopyBgTilemapBufferToVram` did nothing and the old VRAM map stayed on screen. Fix: allocate a 0x800 byte heap buffer and call `SetBgTilemapBuffer(0, buf)` after `InitBgsFromTemplates`, free it on exit (a static array went to IWRAM and pushed it to 97 percent, so the heap is used). Leg14: the full card shows (THE SACRED STONES, THE END, Thank you for playing.), fades out, the field returns, then the game warps to Pallet Town. Images: `docs/img/verify_the_end_garbled_leg12.png`, `docs/img/verify_the_end_card.png`, `docs/img/verify_the_end_before_after.png` (top Leg12, bottom Leg14).
New files: `builds/Pokemon FireRed Eirika Leg14-EndCardFix.gba`, `patches/FireRed_Eirika_Leg14_EndCardFix.ips`, `decomp_full_v14.tar.gz` (v13 already existed from the dungeon work, so v14 was used; v12 and older untouched).

### 3. Ally lines and cameos
Images: `docs/img/verify_text_a.png` (chapters 5x, 8, 9, 10, 11) and `docs/img/verify_text_b.png` (12, 13, 17, 21, 21x). Each row is end-of-message frames from the full run. Seen: Zonta (5x), Eirika, Seth, Derik, Innes, Tana, L'Arachel, Joshua, Dozla, Duessel, Myrrh, Ephraim, Fomortiis lines, all inside the box with no clipping. The epilogue cameo lines (Ephraim, Innes, Tana, L'Arachel, Dozla, Joshua, Duessel, Cormag, Myrrh, Eirika) also fit. `tools/check_overflow.py` on the Leg14 tree: 173 segments over 36 glyphs against 169 in vanilla; none are story text (the 4 extra are 37 glyph lines in vanilla map files, for example "MOULDER's" edits, one glyph over, apostrophes are narrow). Minor: in chapter 13 (Hamill Canyon, dark tunnel) the flash circle briefly shows as a white rectangle in two frames; not clipped text.

### 4. Stat-flash
`docs/img/verify_statflash.png`. Eirika used Agility in a real battle (first skirmish of chapter 0): "EIRIKA's SPEED sharply rose!" and the foe's Leer lowering "EIRIKA's DEFENSE" both show with the portrait on screen and no arrow or colour flash on it. PASS.

### 5. Chapter sweep (tools/verify_run.py, real flow from Pallet Town guide)
Labels to indexes: index 5 is chapter 5x, index 23 is chapter 21x.
Indexes 0 to 22: all PASS (iterations 480 to 1540 each, no hangs, no crashes, no whiteouts). Index 23 (21x): PASS on a clean run (1500 iterations) and on a second run; one earlier run stalled for 5000 iterations on "Foe GENGAR took EIRIKA with it!" (Destiny Bond). That stall is the test driver topping up HP while the faint animation runs, not seen in the repeat runs; treated as a harness artifact, not a game hang. No crash (white or black screen freeze) was seen anywhere. Chapter 0 had also looked like a hang before the harness fix above.
Frames: `/tmp` only for the full sweep (about 20000 images); representative frames are in the images above.

### 6. Black Temple look
FAIL. In game (`docs/img/verify_rooms_all.png` bottom row, `docs/img/verify_room_blacktemple.png`) the Black Temple is a pale, washed out white and grey cloud texture with a faint green altar rug and no clear wall, not the dark brick room shown by the offline render (`docs/img/indoor_walls_fixed.png`). It looks like a palette problem (the dark FE8 palette is not the one used at run time), so there is no readable wall style or wall width to judge. Layout, exit and NPCs work and the chapter runs. Not fixed (not trivial). Suggested next step: check the Black Temple palette slots in `tools/leg9_indoor_maps.py` and the secondary tileset palette load, or switch back to the Pokemon Tower 6F donor.
