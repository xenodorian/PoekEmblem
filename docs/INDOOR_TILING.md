# Indoor tiling rules

`tools/indoor_tiling.py` is the indoor version of the outdoor rule tools in the Pokemon-War-and-Murder repo
(`lawn_rules.py`, `rock_rules.py`, `edge_rules.py`, `retree.py`). You give it a character grid, it picks every block from the
neighbours and refuses layouts that break a rule. Run `python3 tools/indoor_tiling.py selftest`, `render OUT.png [LABELS.png]`
or `emit DIR` (secondary tileset, `map.bin`, collision bits, `room.json`).

## What was read from the outdoor tools
* **Cardinal neighbours pick edge blocks.** `lawn_rules.EDGE` is keyed by which of N, S, E, W is the other region.
* **Two cardinal neighbours pick a concave corner**, **a diagonal-only neighbour picks a convex corner** (`CONVEX`, key = direction of the cell).
* **A table says which blocks may repeat on which axis** (`ROCK_H_OK`, `ROCK_V_OK`), and a validator reports combs, orphans, half trees.
* **An unknown neighbourhood is an error**, never a guess (`border_block` raises). Fences and rock blocks only go on the surface they are drawn for.
* **Fallbacks go through the cardinal part** of a neighbourhood, never through a different shape.

## The indoor rules
Layout legend: space void, `#` FE8 wall, `=` FireRed cream wall, `.` floor, `c` rug, `T` table (2x2), `a`/`b` chairs, `p` tall plant,
`D` door, `w s k f x` wall objects (window, shelf, sink, fridge, cabinet). Row 0 is the wall cap row, row 1 the face row.

1. **Walls from the cell below.** A wall cell with floor below is a *face*, a wall cell with wall below is a *cap*, and a face may run on over side void.
   A face needs a cap above, a cap needs a face below, anything else is "dangling" and rejected. Side and bottom walls are void (FireRed style).
2. **Floor shading is an edge rule** (`EDGE`, `CONVEX`). Non floor on the north makes the top two quadrants of the cell dark, south the bottom two, and so on.
   Dark on two sides is a concave corner (3 quadrants dark), diagonal only is a convex corner (1 quadrant dark), 3 or 4 sides is the union.
   Dark is only a palette swap (palette 8 is palette 7 times 0.8), so no extra tile data is needed.
3. **Floor variants.** `floorB` is an accent: a hash of (x, y, room seed) picks about one cell in five, and a cell never becomes an accent if its west or north neighbour is one, so accents never touch on either axis (`accent_adjacent` in validate()). There is no fixed lattice any more. All other cells use `floorA` or its horizontal, vertical or both mirrored forms (picked by the same hash). The mirrors reuse the same 8x8 tiles through the tile flip bits, so they cost no tile data. Each room passes its own `seed` to `autotile()`.
3b. **Wall end corner blocks.** An FE8 wall cell (`#`, cap or face) with void beside it is a wall end. Its outer column of quadrants uses palette 10 (the wall palette times 0.65), so the end of a wall reads as a shaded corner. Again a palette swap only (key = void west / void east, like the floor EDGE table).
4. **Rug** (`RUG_EDGE`): key = (N, S, E, W) is not rug. One missing side gives an edge block (68, 92, 86, 83), two give a corner (67, 70, 91, 94),
   none gives the centre (69). A one cell wide rug, or a rug with an inner corner (diagonal-only gap), has no FireRed block and is **rejected**.
5. **Door.** `D` must sit on the last row. The 3 cells above it must be plain floor and become the mat (18, 19, 20), the 3 cells of the last row become 26, 27, 28
   (the flanks must be void). The cells in front of the mat must stay walkable.
6. **Wall objects** (window, shelf, sink, fridge, cabinet) go on the face row only, on cream panel only (cap row above must be `=`), runs must be a multiple of the
   object width, floor below must be floor, the cell two below must be free (access). Their cap, face and floor row blocks come from one table (`WALL_OBJ`).
   Cream and FE8 wall may meet at a vertical seam, but objects never touch the FE8 wall.
7. **Tall plant** = pot cell (solid) with the plant top (walkable) above it. It picks the left or right variant by which half of the room it stands in (leaves face the centre).
8. **Table** is a 2x2 block on rug (its bottom layer is rug). A chair `a` needs a table to its east, `b` a table to its west.
9. **Collision** per block: wall cap, face, void, door row, table and pot are solid. Everything else is open.
10. **validate()**: accent adjacency, wall ends, every walkable cell reachable from the door mat (flood fill), nothing blocks the mat or the cell in front of a wall object,
    and every lifted FireRed block uses primary tiles and palettes only (so it needs no extra tileset).

## How FireRed and FE8 tiles mix (the clean extraction trick)
A FireRed metatile has a bottom layer and a top layer. Furniture, plants and the door mat have the parquet floor in the bottom layer and the object in the top layer
with transparency. `Registry.lift()` replaces exactly those parquet quadrants with the FE8 floor quadrants and keeps the object layer untouched, so any FireRed object
stands on the FE8 floor with no cropping and no mask. Rug blocks are lifted the same way (only the parquet quadrants of the corners and edges change).
Blocks whose bottom layer is wall (windows, shelf, sink, fridge, cabinet) cannot be lifted, so they sit on a FireRed cream wall panel and only their floor row is lifted.

FE8 pieces (no furniture is cropped, each is a 16x16 patch found by a seam search that repeats without a seam):
* floor: `bg_Castle_Interior` (79,44) and (58,45) (stone brick pattern)
* wall face: `bg_Grado_Chamber` (184,140) (wood panel), wall cap: `bg_Castle_Interior` (112,120) (moss course)
Pixels are quantised to 15 colours per group (palette 7 floor, 8 floor shade, 9 wall); the secondary tileset has 17 tiles and 42 metatiles.
FE8 art comes from the decomp's `graphics/bg/*.png` (the game's own backgrounds).

## Known gaps
* No inner rug corner and no one wide runner (FireRed has no blocks for them), so layouts needing them are rejected.
* Wall end corners are a shade only (no true corner art). The FireRed cream panel has no corner blocks at all, so a cream wall must not end beside void: put FE8 wall (`#`) at the ends, as the story maps do.
* FE8 wall style and FireRed cream panel only meet at a straight vertical seam.

## Test room and how it was checked
`tools/indoor_tiling.py render` draws the 15x16 test room offline: `docs/img/indoor_tiling_test.png`, with sources in
`docs/img/indoor_tiling_test_sources.png` (orange FE8, blue FireRed, purple FireRed object lifted onto the FE8 floor).
In the emulator: `emit DIR` wrote the tileset and `map.bin` (copy in `workdata/indoor_tiling_test/`) into a copy of `decomp_full_v6.tar.gz`, replacing the
`Story_BlackTemple` layout (same 15x16 size, same primary tileset) and the new game start warp (temporary, not shipped), then `make -j8` and
`workdata/harness/bin/shot_save` with `workdata/indoor_tiling_test/walk_script.txt`. Screenshots: `docs/img/indoor_tiling_test_emulator.png`.
(After changing a layout .bin, `touch data/layouts/layouts.json` so make rebuilds the layout data.) The test ROM is not committed (ROMs are ignored).

## Where it is used
`tools/leg9_indoor_maps.py DECOMP_DIR` applies it to four story maps (15 x 16 each, door at column 7): Renais Castle (throne hall, red carpet, plants, windows, shelves, cabinets), Frelia Castle (council table on a rug island), Jehanna Hall (dais rug, window) and Black Temple (dark FE8 walls, altar table). It rewrites each map's secondary tileset (17 tiles, under 50 metatiles), `map.bin`, `border.bin`, the `-num_tiles` line in `tileset_rules.mk`, and moves NPCs, the treasure ball and the signs to valid cells (the asserts check: walkable cell, not on the walk in column x = 7 rows 11 to 15, signs on the wall face row with floor below). The exit warp is on the door mat (7,14); the chapter scripts still arrive at (7,15) and walk up 4.
Fort Rigwald and the Grado Throne Room stay on the FireRed League donor interiors (`tools/leg7_donor_maps.py`): the autotiler has no room type for them (no bright hall, no stairs or dais blocks), so it does not clearly beat the donors there.
Run order on a tree: leg4_story_tilesets.py, leg5_story_map_objects.py, leg7_donor_maps.py, leg9_indoor_maps.py (this resets the Black Temple layout to its own if leg7 switched it to a donor), then leg3_story.py. Not emulator checked (owner: build only).

## Wall rules (Leg11)
Added after the owner saw a room with mixed walls and a wall running past the floor. validate() now enforces:
1. One wall style per room. Use `#` (FE8 brick, two rows) or `=` (FireRed cream panel, plus wall objects w s k f x, which only exist on cream). A room never mixes them. Rooms with wall objects use cream; a room with no wall objects may use brick.
2. Wall width equals floor width. Every wall row spans exactly the columns of the floor, with void on both sides. No wall cell over void (the old rule that let a wall run on over the side void is removed), no floor cell whose north neighbour is neither floor nor wall.
3. The floor is a solid rectangle (same column span on every row, no gaps). An L shaped floor is rejected, because the notch edges would need wall coverage the tile set has no blocks for. Make it a rectangle.
Selftest has failing cases for mixed styles, wall past the floor, wall narrower than the floor and an L shaped floor. `tools/render_story_maps.py DECOMP OUT.png` renders all six story maps offline (`docs/img/indoor_walls_fixed.png`).
Rooms now: Renais and Frelia cream, Jehanna and Black Temple brick (no windows or cabinets), all floors 13 wide at columns 1 to 13 of a 15 wide map. Fort Rigwald and the Grado Throne Room use vanilla FireRed League layouts: one wall style each and walls match the floor by construction.
