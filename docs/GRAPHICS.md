# Graphics Import Notes

## Target 1: Eirika (map sprite / portrait)

### FE8 (Sacred Stones BE8E) source
- Portraits are typically in the portrait table (FEBuilderGBA → Portrait Editor).
- Approximate range for unit portraits often around 0x5B0000–0x6x0000 (confirm with FEBuilder or Emblem-Magic).
- Map sprites (standing/walking) in the class/map sprite tables.
- Export as 16-color PNG + palette via FEBuilderGBA (recommended) or GBAGE-style tools.

### FireRed insert plan
- Free space: 0x71A23C (large 0xFF region, ~6 MB)
- Overworld sprites: use HMA Overworld Sprite editor or unLZ + repoint.
- Trainer / battle sprites: insert into sprite tables after palette conversion (16 colors max per sprite).
- Compression: LZ77 (GBA BIOS compatible).

### Status
- Offsets not yet dumped in this sandbox (no FEBuilder binary).
- Next concrete step: local Windows FEBuilder export of Eirika portrait → PNG → document exact pointer + size here → HMA import + IPS.

Update this file when exact pointers are known.
